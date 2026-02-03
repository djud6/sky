import { createContext, useState } from "react";
import InputsForm from "./GHGComponents/InputsForm";
import EmissionResultsSection from "./GHGComponents/EmissionResultsSection";
import CalculationInfoModal from "./GHGComponents/CalculationInfoModal";
import GHGWelcome from "./GHGComponents/GHGWelcome";
import SelectorPage from "./GHGComponents/SelectorPage";
import ProgressBarGHG from "./GHGComponents/ProgressBarGHG";

export const GHGContext = createContext();

const GasEmissionsCalculator = () => {
  const [scope, setScope] = useState(1);
  const [selectedCountry, setSelectedCountry] = useState("");
  const [fleetType, setFleetType] = useState("");
  const [inputs, setInputs] = useState({});
  const [results, setResults] = useState({});
  const [page, setPage] = useState(1); // 1 - WelomePage, 2 - SelectorPage, 3 - InputsForm, 4 - Result

  const value = {
    scope,
    setScope,
    selectedCountry,
    setSelectedCountry,
    fleetType,
    setFleetType,
    inputs,
    setInputs,
    results,
    setResults,
    page,
    setPage,
  };

  return (
    <GHGContext.Provider value={value}>
      <main>
        <ProgressBarGHG />
        {page === 1 && <GHGWelcome />}
        {page === 2 && <SelectorPage />}
        {page === 3 && <InputsForm />}
        {page === 4 && <EmissionResultsSection />}
        <CalculationInfoModal />
      </main>
    </GHGContext.Provider>
  );
};

export default GasEmissionsCalculator;
