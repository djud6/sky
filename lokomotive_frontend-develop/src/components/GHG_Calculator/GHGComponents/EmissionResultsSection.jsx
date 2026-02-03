import React from "react";
import EmissionResultCard from "./EmissionResultCard";
import ResultsActions from "./ResultsActions";

const EmissionResultsSection = () => {
    return (
        <section>
            <ResultsActions />
            <EmissionResultCard />
        </section>
    )
}

export default EmissionResultsSection;