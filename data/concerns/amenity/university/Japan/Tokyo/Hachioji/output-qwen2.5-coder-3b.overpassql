[out:json][timeout:30];
area["name:en"="Hachioji"]->.outer;
(
  nwr["amenity"="university"](area.outer);
);
out geom;
