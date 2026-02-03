const currentDate = () => {
    const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    const today = new Date();
    const dd = String(today.getDate()).padStart(2, '0');
    const mm = monthNames[ today.getMonth() ];
    const yyyy = today.getFullYear();

   return `${mm} ${dd}, ${yyyy}`;
};

export default currentDate;
