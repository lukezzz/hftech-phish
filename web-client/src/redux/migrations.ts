
export const migrations = {
    0.21: (state: any) => {
        // migration to keep only device state
        console.log('Migration Running!')
        return {
            ...state,
            config: {
                remember: true,
                theme: "dark"
            }
        }
    },

}
