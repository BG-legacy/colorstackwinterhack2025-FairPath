/**
 * Data Query Hooks
 * React Query hooks for all GET endpoints related to data/catalog
 */
import { useQuery, UseQueryOptions } from '@tanstack/react-query';
import dataService, {
  CatalogResponse,
  OccupationCatalog,
  DataDictionary,
  DataStats,
  ProcessedDataResponse,
  ProcessedVersionResponse,
  CatalogQueryParams,
} from '../../services/data';

/**
 * Query keys factory for data endpoints
 */
export const dataQueryKeys = {
  all: ['data'] as const,
  catalog: (params?: CatalogQueryParams) => [...dataQueryKeys.all, 'catalog', params] as const,
  occupation: (careerId: string) => [...dataQueryKeys.all, 'occupation', careerId] as const,
  dictionary: () => [...dataQueryKeys.all, 'dictionary'] as const,
  stats: () => [...dataQueryKeys.all, 'stats'] as const,
  processed: (careerId?: string) => [...dataQueryKeys.all, 'processed', careerId] as const,
  processedVersion: () => [...dataQueryKeys.all, 'processed', 'version'] as const,
  processedOccupation: (careerId: string) => [...dataQueryKeys.all, 'processed', 'occupation', careerId] as const,
};

/**
 * Get occupation catalog with pagination and filters
 */
export const useOccupationCatalog = (
  params?: CatalogQueryParams,
  options?: Omit<UseQueryOptions<CatalogResponse>, 'queryKey' | 'queryFn'>
) => {
  return useQuery({
    queryKey: dataQueryKeys.catalog(params),
    queryFn: () => dataService.getOccupationCatalog(params),
    staleTime: 5 * 60 * 1000, // 5 minutes - catalog doesn't change often
    gcTime: 30 * 60 * 1000, // 30 minutes
    ...options,
  });
};

/**
 * Get specific occupation by career_id
 */
export const useOccupationById = (
  careerId: string,
  options?: Omit<UseQueryOptions<OccupationCatalog>, 'queryKey' | 'queryFn'>
) => {
  return useQuery({
    queryKey: dataQueryKeys.occupation(careerId),
    queryFn: () => dataService.getOccupationById(careerId),
    enabled: !!careerId, // Only fetch if careerId is provided
    staleTime: 10 * 60 * 1000, // 10 minutes
    gcTime: 60 * 60 * 1000, // 1 hour
    ...options,
  });
};

/**
 * Get data dictionary
 */
export const useDataDictionary = (
  options?: Omit<UseQueryOptions<DataDictionary[]>, 'queryKey' | 'queryFn'>
) => {
  return useQuery({
    queryKey: dataQueryKeys.dictionary(),
    queryFn: () => dataService.getDataDictionary(),
    staleTime: 60 * 60 * 1000, // 1 hour - dictionary rarely changes
    gcTime: 24 * 60 * 60 * 1000, // 24 hours
    ...options,
  });
};

/**
 * Get data statistics
 */
export const useDataStats = (
  options?: Omit<UseQueryOptions<DataStats>, 'queryKey' | 'queryFn'>
) => {
  return useQuery({
    queryKey: dataQueryKeys.stats(),
    queryFn: () => dataService.getDataStats(),
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 30 * 60 * 1000, // 30 minutes
    ...options,
  });
};

/**
 * Get processed data
 */
export const useProcessedData = (
  careerId?: string,
  options?: Omit<UseQueryOptions<ProcessedDataResponse>, 'queryKey' | 'queryFn'>
) => {
  return useQuery({
    queryKey: dataQueryKeys.processed(careerId),
    queryFn: () => dataService.getProcessedData(careerId),
    staleTime: 10 * 60 * 1000, // 10 minutes
    gcTime: 60 * 60 * 1000, // 1 hour
    ...options,
  });
};

/**
 * Get processed data version
 */
export const useProcessedDataVersion = (
  options?: Omit<UseQueryOptions<ProcessedVersionResponse>, 'queryKey' | 'queryFn'>
) => {
  return useQuery({
    queryKey: dataQueryKeys.processedVersion(),
    queryFn: () => dataService.getProcessedDataVersion(),
    staleTime: 60 * 60 * 1000, // 1 hour
    gcTime: 24 * 60 * 60 * 1000, // 24 hours
    ...options,
  });
};

/**
 * Get processed occupation data
 */
export const useProcessedOccupation = (
  careerId: string,
  options?: Omit<UseQueryOptions<{ version: string; processed_date?: string; occupation: any }>, 'queryKey' | 'queryFn'>
) => {
  return useQuery({
    queryKey: dataQueryKeys.processedOccupation(careerId),
    queryFn: () => dataService.getProcessedOccupation(careerId),
    enabled: !!careerId,
    staleTime: 10 * 60 * 1000, // 10 minutes
    gcTime: 60 * 60 * 1000, // 1 hour
    ...options,
  });
};




