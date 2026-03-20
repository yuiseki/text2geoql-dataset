[out:json][timeout:30];
area["name:en"="Nishitokyo"]->.outer;
(
  nwr["amenity"="university"](area.outer);
);
out geom;
