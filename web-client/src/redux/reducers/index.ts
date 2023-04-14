import { combineReducers } from "redux";
import configReducer from "./configSlice";
// import dagReducer from './dagReducer'
import { baseApi } from '@/services/base'

export const rootReducer = combineReducers({
    config: configReducer,
    [baseApi.reducerPath]: baseApi.reducer,
});
