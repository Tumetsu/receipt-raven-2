import Axios, { AxiosRequestConfig } from 'axios';

import { API_BASE_URL } from './base-url';

/**
 * The one HTTP client of the app. The generated client in `./generated` calls
 * it through `axiosInstance` (configured as orval's mutator), so request-wide
 * concerns such as auth headers or error reporting belong here.
 */
export const AXIOS_INSTANCE = Axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const axiosInstance = <T>(config: AxiosRequestConfig): Promise<T> =>
  AXIOS_INSTANCE(config).then(({ data }) => data as T);
