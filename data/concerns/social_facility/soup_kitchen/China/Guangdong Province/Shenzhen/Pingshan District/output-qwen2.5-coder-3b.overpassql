[out:json][timeout:30];
area["name:en"="Shenzhen"]->.outer;
area["name:en"="Guangdong Province"]->.inner;
(
  nwr["amenity"="food_court"](area.inner)(area.outer);
);
out geom;
