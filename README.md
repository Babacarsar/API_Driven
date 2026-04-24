------------------------------------------------------------------------------------------------------
ATELIER API-DRIVEN INFRASTRUCTURE
------------------------------------------------------------------------------------------------------
L’idée en 30 secondes : **Orchestration de services AWS via API Gateway et Lambda dans un environnement émulé**.  
Cet atelier propose de concevoir une architecture **API-driven** dans laquelle une requête HTTP déclenche, via **API Gateway** et une **fonction Lambda**, des actions d’infrastructure sur des **instances EC2**, le tout dans un **environnement AWS simulé avec LocalStack** et exécuté dans **GitHub Codespaces**. L’objectif est de comprendre comment des services cloud serverless peuvent piloter dynamiquement des ressources d’infrastructure, indépendamment de toute console graphique.Cet atelier propose de concevoir une architecture API-driven dans laquelle une requête HTTP déclenche, via API Gateway et une fonction Lambda, des actions d’infrastructure sur des instances EC2, le tout dans un environnement AWS simulé avec LocalStack et exécuté dans GitHub Codespaces. L’objectif est de comprendre comment des services cloud serverless peuvent piloter dynamiquement des ressources d’infrastructure, indépendamment de toute console graphique.
  
-------------------------------------------------------------------------------------------------------
Séquence 1 : Codespace de Github
-------------------------------------------------------------------------------------------------------
Objectif : Création d'un Codespace Github  
Difficulté : Très facile (~5 minutes)
-------------------------------------------------------------------------------------------------------
RDV sur Codespace de Github : <a href="https://github.com/features/codespaces" target="_blank">Codespace</a> **(click droit ouvrir dans un nouvel onglet)** puis créer un nouveau Codespace qui sera connecté à votre Repository API-Driven.
  
---------------------------------------------------
Séquence 2 : Création de l'environnement AWS (LocalStack)
---------------------------------------------------
Objectif : Créer l'environnement AWS simulé avec LocalStack  
Difficulté : Simple (~5 minutes)
---------------------------------------------------

Dans le terminal du Codespace copier/coller les codes ci-dessous etape par étape :  

**Installation de l'émulateur LocalStack**  
```
sudo -i mkdir rep_localstack
```
```
sudo -i python3 -m venv ./rep_localstack
```
```
sudo -i pip install --upgrade pip && python3 -m pip install localstack && export S3_SKIP_SIGNATURE_VALIDATION=0
```
```
localstack start -d
```
**vérification des services disponibles**  
```
localstack status services
```
**Réccupération de l'API AWS Localstack** 
Votre environnement AWS (LocalStack) est prêt. Pour obtenir votre AWS_ENDPOINT cliquez sur l'onglet **[PORTS]** dans votre Codespace et rendez public votre port **4566** (Visibilité du port).
Réccupérer l'URL de ce port dans votre navigateur qui sera votre ENDPOINT AWS (c'est à dire votre environnement AWS).
Conservez bien cette URL car vous en aurez besoin par la suite.  

Pour information : IL n'y a rien dans votre navigateur et c'est normal car il s'agit d'une API AWS (Pas un développement Web type UX).

---------------------------------------------------
Séquence 3 : Exercice
---------------------------------------------------
Objectif : Piloter une instance EC2 via API Gateway
Difficulté : Moyen/Difficile (~2h)
---------------------------------------------------  
Votre mission (si vous l'acceptez) : Concevoir une architecture **API-driven** dans laquelle une requête HTTP déclenche, via **API Gateway** et une **fonction Lambda**, lancera ou stopera une **instance EC2** déposée dans **environnement AWS simulé avec LocalStack** et qui sera exécuté dans **GitHub Codespaces**. [Option] Remplacez l'instance EC2 par l'arrêt ou le lancement d'un Docker.  

**Architecture cible :** Ci-dessous, l'architecture cible souhaitée.   
  
![Screenshot Actions](API_Driven.png)   
  
---------------------------------------------------  
# API Driven Infrastructure — LocalStack (EC2 + Lambda + API Gateway)

## 1. Objectif

Ce projet met en place une architecture inspirée d’AWS en local grâce à **LocalStack**.

L’objectif est de :

- Simuler une instance EC2
- Créer une fonction Lambda pour piloter cette instance
- Exposer cette fonction via une API Gateway
- Interagir avec l’infrastructure via HTTP (API)

---

## 2. Architecture

Utilisateur → API Gateway → Lambda → EC2 (LocalStack)

- API Gateway : point d’entrée HTTP
- Lambda : logique métier (start / stop / describe)
- EC2 : ressource simulée

---

## 3. Prérequis

Installer :

```bash
sudo apt update
sudo apt install -y curl unzip zip python3-pip

Installer AWS CLI :

curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "/tmp/awscliv2.zip"
unzip -o /tmp/awscliv2.zip -d /tmp
sudo /tmp/aws/install

Installer LocalStack :

pip install localstack awscli-local
4. Lancer LocalStack
localstack start -d

Vérifier :

docker ps
5. Configuration AWS (fake)
aws configure

Mettre :

Access key: test
Secret key: test
Region: us-east-1
6. Création de l’instance EC2

Lister les images disponibles :

awslocal ec2 describe-images

Créer une instance :

awslocal ec2 run-instances \
  --image-id ami-03cf127a \
  --count 1 \
  --instance-type t2.micro

Récupérer son ID :

INSTANCE_ID=$(awslocal ec2 describe-instances \
  --query "Reservations[0].Instances[0].InstanceId" \
  --output text)

echo $INSTANCE_ID
7. Création de la Lambda

Créer le fichier :

mkdir lambda
nano lambda/lambda_function.py

Code :

import json
import boto3

def handler(event, context):
    ec2 = boto3.client(
        "ec2",
        endpoint_url="http://host.docker.internal:4566",
        region_name="us-east-1",
        aws_access_key_id="test",
        aws_secret_access_key="test"
    )

    body = event.get("body", event)

    if isinstance(body, str):
        body = json.loads(body)

    action = body.get("action", "describe")
    instance_id = body.get("instance_id")

    if action == "describe":
        return {
            "statusCode": 200,
            "body": json.dumps(ec2.describe_instances(), default=str)
        }

    if action == "start":
        ec2.start_instances(InstanceIds=[instance_id])
        return {
            "statusCode": 200,
            "body": json.dumps({"status": "started"})
        }

    if action == "stop":
        ec2.stop_instances(InstanceIds=[instance_id])
        return {
            "statusCode": 200,
            "body": json.dumps({"status": "stopped"})
        }

    return {
        "statusCode": 400,
        "body": json.dumps({"error": "invalid action"})
    }

Zip :

cd lambda
zip function.zip lambda_function.py
cd ..

Créer la Lambda :

awslocal lambda create-function \
  --function-name ec2-control \
  --runtime python3.11 \
  --handler lambda_function.handler \
  --zip-file fileb://lambda/function.zip \
  --role arn:aws:iam::000000000000:role/lambda-role

Test Lambda :

awslocal lambda invoke \
  --function-name ec2-control \
  --cli-binary-format raw-in-base64-out \
  --payload '{"action":"describe"}' \
  response.json

cat response.json
8. Création API Gateway

Créer API :

awslocal apigateway create-rest-api --name "ec2-api"

Récupérer ID :

API_ID=$(awslocal apigateway get-rest-apis --query "items[0].id" --output text)

Root :

ROOT_ID=$(awslocal apigateway get-resources \
  --rest-api-id $API_ID \
  --query "items[0].id" \
  --output text)

Créer route :

RESOURCE_ID=$(awslocal apigateway create-resource \
  --rest-api-id $API_ID \
  --parent-id $ROOT_ID \
  --path-part control \
  --query "id" \
  --output text)

Méthode POST :

awslocal apigateway put-method \
  --rest-api-id $API_ID \
  --resource-id $RESOURCE_ID \
  --http-method POST \
  --authorization-type NONE

Intégration Lambda :

awslocal apigateway put-integration \
  --rest-api-id $API_ID \
  --resource-id $RESOURCE_ID \
  --http-method POST \
  --type AWS_PROXY \
  --integration-http-method POST \
  --uri arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:000000000000:function:ec2-control/invocations

Déployer :

awslocal apigateway create-deployment \
  --rest-api-id $API_ID \
  --stage-name dev
9. Tests

Lister EC2 via API :

curl -X POST "http://localhost:4566/restapis/$API_ID/dev/_user_request_/control" \
  -H "Content-Type: application/json" \
  -d '{"action":"describe"}'

Stop instance :

curl -X POST "http://localhost:4566/restapis/$API_ID/dev/_user_request_/control" \
  -H "Content-Type: application/json" \
  -d "{\"action\":\"stop\",\"instance_id\":\"$INSTANCE_ID\"}"

Start instance :

curl -X POST "http://localhost:4566/restapis/$API_ID/dev/_user_request_/control" \
  -H "Content-Type: application/json" \
  -d "{\"action\":\"start\",\"instance_id\":\"$INSTANCE_ID\"}"

Vérification :

awslocal ec2 describe-instances \
  --query "Reservations[0].Instances[0].State.Name" \
  --output text

Résultat :

running
