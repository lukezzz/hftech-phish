import { QueryReturnValue } from '@reduxjs/toolkit/dist/query/baseQueryTypes';
import {
    BaseQueryFn,
    createApi,
    FetchArgs,
    fetchBaseQuery,
    FetchBaseQueryError,
    FetchBaseQueryMeta,
} from '@reduxjs/toolkit/query/react';
// import { handleReqError, printPanel } from './errorHandle'
// import { notification } from 'antd';
import { notification } from '@/redux/error'


const baseUrl: string = import.meta.env.VITE_API_URL as string;

// 定义返回数据类型
interface IResultData {
    success: boolean;
    errorMessage?: string;
    data?: Record<string, unknown> | number | string;
}

type NotificationType = 'success' | 'info' | 'warning' | 'error';

interface Error422 {
    loc: string[]
    msg: string
    type: string
}

interface ErrorData {
    success: boolean
    data?: string,
    errorMessage?: string | Error422[]
    traceId?: string
    app?: string
}

// const openNotificationWithIcon = (type: NotificationType, message: string) => {
//     notification[type]({
//         message: 'Error',
//         description: message
//     });
// };

const baseQuery = fetchBaseQuery({
    baseUrl: baseUrl,
    prepareHeaders: (headers, { getState }) => {
        // const token = (getState() as RootState).auth.token;
        // headers.set('token', '97aca8cabd58406db9afc7a094a57584');
        return headers;
    },
});



const baseQueryWithIntercept: BaseQueryFn<
    string | FetchArgs,
    unknown,
    FetchBaseQueryError
> = async (args, api, extraOptions) => {
    const result: QueryReturnValue<any, FetchBaseQueryError, FetchBaseQueryMeta> =
        await baseQuery(args, api, extraOptions);
    // console.log(result, '拦击器');
    const { data, error, meta } = result;
    const { request } = meta as FetchBaseQueryMeta;
    const url: string = request.url;
    // 如果遇到httpStatus!=200-300错误的时候
    if (error) {
        // 根据状态来处理错误
        // const { status } = error as FetchBaseQueryError;
        const errorData = error.data as ErrorData
        // console.log(errorData)
        // handleReqError(Number(status), url, errorData.errorMessage);

        console.log(errorData)
        // type of error.message is Error422
        let errorMsg = ""
        if (errorData.errorMessage instanceof Array) {
            const error422 = errorData.errorMessage[0]
            errorMsg = error422.msg
        } else {
            errorMsg = errorData.errorMessage as string
        }

        return Promise.reject(errorMsg);
    }
    // 正确的时候，根据各自后端约定来写的
    const { success, errorMessage } = data as IResultData;
    if (success) {
        return result;
    } else {
        if (result) return result
        throw new TypeError(errorMessage)
    }
};

export const baseApi = createApi({
    baseQuery: baseQueryWithIntercept,
    reducerPath: 'baseApi',
    // 缓存时间，以秒为单位，默认是60秒
    // keepUnusedDataFor: 2 * 60,
    // refetchOnMountOrArgChange: 30 * 60,
    tagTypes: ['User'],
    endpoints: () => ({}),
});


