import type { SearchStringType } from "./TableProps";
import { ProColumns } from "@ant-design/pro-table";
import { i18n } from "i18next";

export const setPropsFilter = (filters: any, curFilter: any) => {
    if (
        !curFilter ||
        !curFilter.and ||
        Object.keys(curFilter.and).length === 0
    ) {
        let newFilter = { and: {} };
        Object.keys(filters).forEach((key) => {
            if (filters[key]) {
                // @ts-ignore
                newFilter.and[`${key}.id`] = { in: filters[key] };
            }
            delete filters[key];
        });
        return newFilter;
    } else {
        Object.keys(filters).forEach((key) => {
            if (curFilter["and"][`${key}.id`] && !filters[key]) {
                delete curFilter["and"][`${key}.id`];
            }
            if (filters[key]) {
                curFilter["and"][`${key}.id`] = { in: filters[key] };
            }
        });

        return curFilter;
    }
};

export const setFormFilter = (filters: any, curFilter: any) => {
    if (
        !curFilter ||
        !curFilter.and ||
        Object.keys(curFilter.and).length === 0
    ) {
        let newFilter = { and: {} };
        Object.keys(filters).forEach((key) => {
            if (filters[key]) {
                // @ts-ignore
                newFilter.and[key] = { like: `%${filters[key]}%` };
            }
        });
        return newFilter;
    } else {
        if (Object.keys(filters).length === 0) {
            curFilter["and"] = {}
        }
        Object.keys(filters).forEach((key) => {
            if (curFilter["and"][key] && !filters[key]) {
                delete curFilter["and"][key];
            }
            if (filters[key]) {
                curFilter["and"][key] = { like: `%${filters[key]}%` };
            }
        });

        return curFilter;
    }
};


export const formatSorter = (sorter: any) => {
    let sort = {};
    Object.keys(sorter).map((k) => {
        if (sorter.order === "ascend") {
            sort = { ...sort, [sorter.field]: "asc" };
        } else if (sorter.order === "descend") {
            sort = { ...sort, [sorter.field]: "desc" };
        } else {
            // @ts-ignore
            delete sort[sorter.field];
        }
        return k
    });
    return sort;
};

export const formatSearchQuery = ({
    current,
    pageSize,
    query,
}: SearchStringType) => {
    const newQueryParameters: URLSearchParams = new URLSearchParams();

    newQueryParameters.set("current", current?.toString() || "1");
    newQueryParameters.set("pageSize", pageSize?.toString() || "10");
    if (query && query.filter) {
        newQueryParameters.set("query", JSON.stringify(query));
    }

    return newQueryParameters;
};


export const coli18n = (columns: ProColumns<any>[], i18n: i18n, namespaces: string) => {
    let newCol: ProColumns<any>[] = []
    columns.map((col) => {
        newCol.push({
            ...col,
            // @ts-ignore
            title: i18n.t(`${col.title}`, { ns: namespaces })
        })
        return col
    })
    return newCol
}