import { useContext } from "react";
import { GHGContext } from "../GasEmissionsCalculator";

const RegionSelector = () => {
    const { selectedCountry, setSelectedCountry } = useContext(GHGContext);

    // Temporary contries Array
    const countries = [
        "Afghanistan",
        "Brazil",
        "Canada",
        "China",
        "France",
        "Germany",
        "India",
        "Japan",
        "Mexico",
        "United Kingdom",
        "United States"
    ]

    // // Generate country list automatically
    // const countries = useMemo(() => {
    //     const regionNames = new Intl.DisplayNames(["en"], { type: "region" });
    //     // ISO 3166-1 alpha-2 country codes
    //     const countryCodes = Intl.supportedValuesOf("region").filter(code => /^[A-Z]{2}$/.test(code));
    //     return countryCodes.map(code => regionNames.of(code)).sort();
    // }, []);

    return (
        <select
            className="form-control"
            autoComplete="country"
            id="country"
            name="country"
            value={selectedCountry}
            onChange={(event) => setSelectedCountry(event.target.value)}
        >
            <option value="">Select country</option>
            {countries.map((country) => (
                <option key={country} value={country}>
                    {country}
                </option>
            ))}
        </select>
    );
};

export default RegionSelector;
