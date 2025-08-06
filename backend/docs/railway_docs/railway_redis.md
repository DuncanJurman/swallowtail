Deployed Service
Upon deployment, you will have a Redis service running in your project, deployed from the bitnami/redis Docker image.

Connect
Connect to the Redis server from another service in your project by referencing the environment variables made available in the Redis service:

REDISHOST
REDISUSER
REDISPORT
REDISPASSWORD
REDIS_URL


Backup and Monitoring
Especially for production environments, performing backups and monitoring the health of your data is essential. Consider adding:

Backups: Automate regular backups to ensure data recovery in case of failure. We suggest checking out our native Backups feature.

Observability: Implement monitoring for insights into performance and health of your Redis cluster. You can integrate a Redis exporter for Prometheus, although we do not provide a specific template at this time.

