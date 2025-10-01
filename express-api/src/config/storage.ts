import { Client } from 'minio';
import { config } from './environment';
import { logger } from '../utils/logger';

export class StorageService {
  private client: Client;
  private bucketName: string;

  constructor() {
    this.client = new Client({
      endPoint: config.minio.endpoint,
      port: config.minio.port,
      useSSL: config.minio.useSSL,
      accessKey: config.minio.accessKey,
      secretKey: config.minio.secretKey,
    });
    this.bucketName = config.minio.bucketName;
  }

  async initialize(): Promise<void> {
    try {
      // Check if bucket exists, create if it doesn't
      const bucketExists = await this.client.bucketExists(this.bucketName);
      if (!bucketExists) {
        await this.client.makeBucket(this.bucketName, 'us-east-1');
        logger.info(`Bucket '${this.bucketName}' created successfully`);
      } else {
        logger.info(`Bucket '${this.bucketName}' already exists`);
      }
    } catch (error) {
      logger.error('Error initializing storage service:', error);
      throw error;
    }
  }

  async uploadFile(fileName: string, fileBuffer: Buffer, contentType: string): Promise<string> {
    try {
      const metadata = {
        'Content-Type': contentType,
        'Upload-Date': new Date().toISOString(),
      };

      await this.client.putObject(this.bucketName, fileName, fileBuffer, fileBuffer.length, metadata);
      logger.info(`File '${fileName}' uploaded successfully`);
      return fileName;
    } catch (error) {
      logger.error(`Error uploading file '${fileName}':`, error);
      throw error;
    }
  }

  async downloadFile(fileName: string): Promise<Buffer> {
    try {
      const stream = await this.client.getObject(this.bucketName, fileName);
      const chunks: Buffer[] = [];
      
      return new Promise((resolve, reject) => {
        stream.on('data', (chunk) => chunks.push(chunk));
        stream.on('end', () => resolve(Buffer.concat(chunks)));
        stream.on('error', reject);
      });
    } catch (error) {
      logger.error(`Error downloading file '${fileName}':`, error);
      throw error;
    }
  }

  async deleteFile(fileName: string): Promise<void> {
    try {
      await this.client.removeObject(this.bucketName, fileName);
      logger.info(`File '${fileName}' deleted successfully`);
    } catch (error) {
      logger.error(`Error deleting file '${fileName}':`, error);
      throw error;
    }
  }

  async fileExists(fileName: string): Promise<boolean> {
    try {
      await this.client.statObject(this.bucketName, fileName);
      return true;
    } catch (error) {
      return false;
    }
  }
}

export const storageService = new StorageService();
