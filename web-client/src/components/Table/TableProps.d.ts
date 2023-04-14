export type QueryType = {
    filter: any;
    sort?: any;
};

export type SearchStringType = {
    current?: string | undefined;
    pageSize?: string | undefined;
    query?: QueryType;
};
