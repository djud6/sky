import React, { useContext } from "react";
import { GHGContext } from "../GasEmissionsCalculator";

const EmissionScopeTabs = () => {
    const { scope, setScope } = useContext(GHGContext);
    const scopes = [1, 2, 3, 4];

    return (
        <select
            className="form-control"
            id="scope"
            name="scope"
            value={scope}
            onChange={(event) => setScope(Number(event.target.value))}
        >
            <option value="">Select the scope</option>
            {/* s = scope */}
            {scopes.map((s) => (
                <option key={s} value={s}>
                    {s}
                </option>
            ))}
        </select>
    );
};

export default EmissionScopeTabs;
