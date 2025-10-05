import dotenv from 'dotenv';

dotenv.config();

export const config = {
  port: parseInt(process.env.PORT || '3000', 10),
  nodeEnv: process.env.NODE_ENV || 'development',
  internalApiKey: process.env.INTERNAL_API_KEY || 'your-internal-key',

  database: {
    host: process.env.DB_HOST || 'localhost',
    port: parseInt(process.env.DB_PORT || '5432', 10),
    username: process.env.DB_USERNAME || 'postgres',
    password: process.env.DB_PASSWORD || 'password',
    name: process.env.DB_NAME || 'chatbot_control_panel',
  },

  superAdmin: {
    name: process.env.SUPER_NAME || 'Admin',
    username: process.env.SUPER_USERNAME || 'admin',
    password: process.env.SUPER_PASSWORD || 'admin',
  },
  
  jwt: {
    secret: process.env.JWT_SECRET || 'your-super-secret-jwt-key-change-this-in-production',
    expiresIn: process.env.JWT_EXPIRES_IN || '24h',
  },

  features: {
    division: process.env.DIVISION || false,
    defaultDivisionName: process.env.DEFAULT_DIVISION_NAME || 'Default',
  },
  
  minio: {
    endpoint: process.env.MINIO_ENDPOINT || 'localhost',
    port: parseInt(process.env.MINIO_PORT || '9000', 10),
    accessKey: process.env.MINIO_ACCESS_KEY || 'minioadmin',
    secretKey: process.env.MINIO_SECRET_KEY || 'minioadmin',
    bucketName: process.env.MINIO_BUCKET_NAME || 'documents',
    useSSL: process.env.MINIO_USE_SSL === 'true',
  },
  
  fastapi: {
    url: process.env.FASTAPI_URL || 'http://localhost:8000',
  },
  
  logging: {
    level: process.env.LOG_LEVEL || 'info',
  },
};
