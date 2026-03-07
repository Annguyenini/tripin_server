
const styleSwitcher =(map)=>{
    const STYLES = {
    dark:      'mapbox://styles/mapbox/dark-v11',
    streets:   'mapbox://styles/mapbox/streets-v12',
    satellite: 'mapbox://styles/mapbox/satellite-streets-v12',
};
    const styleBtns = { dark: 'style-dark', streets: 'style-streets', satellite: 'style-satellite' };
    Object.entries(styleBtns).forEach(([key, btnId]) => {
    document.getElementById(btnId).onclick = () => {
        map.setStyle(STYLES[key]);
        document.querySelectorAll('.style-btn').forEach(b => b.classList.remove('active'));
        document.getElementById(btnId).classList.add('active');
    };
});}