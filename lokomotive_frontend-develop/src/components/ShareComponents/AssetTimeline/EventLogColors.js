const eventLogColors = (data) => {
    let color;
    switch (data) {
        case "repair":
            color = "#388e3C";
            break;
        case "operator check":
            color = "#ffa800";
            break;
        case "maintenance":
            color = "#0097a7";
            break;
        case "issue":
            color = "#C2185B";
            break;
        case "disposal":
            color = "#A0A0A0";
            break;
        case "accident":
            color = "#512da8";
            break;
        case "maintenance rule":
            color = "#F57c00";
            break;
        case "transfer":
            color = "#b68d40";
            break;
        default:
            color = "#1976d2";
    };
    return color;
};

export default eventLogColors;