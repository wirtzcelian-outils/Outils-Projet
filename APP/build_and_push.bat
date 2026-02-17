@echo off
set DOCKER_USERNAME=tempddaw

echo.
echo ==========================================
echo Construction de l'image Backend...
echo ==========================================
docker build -t %DOCKER_USERNAME%/app-backend:latest -f backend/Dockerfile.prod backend

echo.
echo ==========================================
echo Construction de l'image Frontend...
echo ==========================================
docker build -t %DOCKER_USERNAME%/app-frontend:latest -f frontend/Dockerfile.prod frontend

echo.
echo ==========================================
echo Connexion a Docker Hub...
echo ==========================================
docker login

echo.
echo ==========================================
echo Push des images vers Docker Hub...
echo ==========================================
docker push %DOCKER_USERNAME%/app-backend:latest
docker push %DOCKER_USERNAME%/app-frontend:latest

echo.
echo ==========================================
echo Termine ! Vous pouvez maintenant utiliser docker-compose.prod.yml
echo N'oubliez pas de mettre a jour le fichier .env si necessaire.
echo Pour lancer en prod : 
echo docker-compose -f docker-compose.prod.yml up -d
echo ==========================================
pause
