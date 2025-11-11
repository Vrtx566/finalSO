#!/usr/bin/env bash
set -euo pipefail

################################################################################
# Script: config.sh
# Propósito: Construir una imagen Docker, etiquetarla (latest por defecto) y
#            subirla al AWS ECR (Elastic Container Registry).
# Uso mínimo:
#   ./config.sh -a <AWS_ACCOUNT_ID> -r <AWS_REGION> -n <ECR_REPO_NAME> -i <IMAGE_NAME>
# Opciones:
#   -a AWS account id (ej: 123456789012)
#   -r AWS region (ej: us-east-1)
#   -n ECR repository name (ej: my-repo)
#   -i local image name (ej: my-app)
#   -t tag (default: latest)
#   -f Dockerfile path (default: Dockerfile)
#   -c build context (default: .)
#   --no-create-repo  no crear repo ECR si no existe
# Requisitos:
#   - aws CLI v2 configurado con credenciales con permisos para ECR
#   - docker instalado y funcionando
################################################################################

AWS_ACCOUNT_ID="802655955683"
AWS_REGION="us-east-1"
ECR_REPO_NAME="so/final-so"
IMAGE_NAME=""
TAG="latest"
DOCKERFILE="Dockerfile"
BUILD_CONTEXT="."
NO_CREATE_REPO=false

usage() {
	sed -n '1,120p' "$0" | sed -n '3,22p'
	echo
	echo "Ejemplo: $0 -a 123456789012 -r us-east-1 -n my-repo -i my-app -t latest"
	exit 1
}

while [[ ${#} -gt 0 ]]; do
	case "$1" in
		-a) AWS_ACCOUNT_ID="$2"; shift 2;;
		-r) AWS_REGION="$2"; shift 2;;
		-n) ECR_REPO_NAME="$2"; shift 2;;
		-i) IMAGE_NAME="$2"; shift 2;;
		-t) TAG="$2"; shift 2;;
		-f) DOCKERFILE="$2"; shift 2;;
		-c) BUILD_CONTEXT="$2"; shift 2;;
		--no-create-repo) NO_CREATE_REPO=true; shift 1;;
		-h|--help) usage;;
		*) echo "Opción desconocida: $1"; usage;;
	esac
done

if [[ -z "$AWS_ACCOUNT_ID" || -z "$AWS_REGION" || -z "$ECR_REPO_NAME" ]]; then
	echo "Faltan parámetros obligatorios (AWS_ACCOUNT_ID, AWS_REGION o ECR_REPO_NAME)." >&2
	usage
fi

# Si no se proporciona IMAGE_NAME, intentamos derivarlo desde app.py (FastAPI title)
if [[ -z "$IMAGE_NAME" ]]; then
	if [[ -f "app.py" ]]; then
		# Extraer title de FastAPI: FastAPI(title="...")
		title=$(grep -Po "FastAPI\\([^)]*title\\s*=\\s*['\"]\\K[^'\"]+" app.py || true)
		if [[ -n "$title" ]]; then
			# Normalizar: minúsculas, caracteres no alfanum -> '-', quitar '-' al inicio/fin
			IMAGE_NAME=$(echo "$title" | tr '[:upper:]' '[:lower:]' | sed -E "s/[^a-z0-9]+/-/g" | sed -E "s/^-|-$//g")
			echo "IMAGE_NAME derivado de app.py (FastAPI title): $IMAGE_NAME"
		else
			IMAGE_NAME=$(basename "$PWD")
			echo "No se encontró title en app.py; usando nombre de directorio: $IMAGE_NAME"
		fi
	else
		echo "No se proporcionó -i y no se encontró app.py; no se puede derivar IMAGE_NAME" >&2
		usage
	fi
fi

command -v aws >/dev/null 2>&1 || { echo "aws CLI no encontrado. Instale/configure aws CLI v2." >&2; exit 2; }
command -v docker >/dev/null 2>&1 || { echo "docker no está instalado o no está en PATH." >&2; exit 2; }

ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
LOCAL_TAG="${IMAGE_NAME}:${TAG}"
ECR_TAG="${ECR_URI}/${ECR_REPO_NAME}:${TAG}"

echo "AWS ECR URI: $ECR_URI"
echo "Construyendo imagen local: $LOCAL_TAG (Dockerfile: $DOCKERFILE, contexto: $BUILD_CONTEXT)"

if [[ ! -f "$DOCKERFILE" ]]; then
	echo "Dockerfile no encontrado en '$DOCKERFILE'." >&2
	exit 3
fi

echo "Ejecutando: docker build -t $LOCAL_TAG -f $DOCKERFILE $BUILD_CONTEXT"
docker build -t "$LOCAL_TAG" -f "$DOCKERFILE" "$BUILD_CONTEXT"

# Login a ECR
echo "Obteniendo credenciales y efectuando login a ECR ($ECR_URI)"
aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "$ECR_URI"

# Crear repo si no existe (opcional según flag)
if [[ "$NO_CREATE_REPO" = false ]]; then
	echo "Comprobando si el repositorio ECR '$ECR_REPO_NAME' existe..."
	if ! aws ecr describe-repositories --repository-names "$ECR_REPO_NAME" --region "$AWS_REGION" >/dev/null 2>&1; then
		echo "Repositorio no encontrado. Creando repo ECR: $ECR_REPO_NAME"
		aws ecr create-repository --repository-name "$ECR_REPO_NAME" --region "$AWS_REGION" >/dev/null
		echo "Repositorio creado."
	else
		echo "Repositorio existente."
	fi
else
	echo "--no-create-repo: no se creará el repositorio si no existe. Se asume que ya existe en ECR."
fi

echo "Etiquetando imagen para ECR: $ECR_TAG"
docker tag "$LOCAL_TAG" "$ECR_TAG"

echo "Subiendo imagen a ECR: $ECR_TAG"
docker push "$ECR_TAG"

echo "Imagen subida con éxito: $ECR_TAG"

exit 0

