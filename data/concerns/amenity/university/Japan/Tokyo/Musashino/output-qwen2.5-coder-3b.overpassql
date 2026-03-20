[out:json][timeout:30];
area["name:en"="Tokyo"]->.outer;
(
  nwr["amenity"="university"](area.outer);
);
out geom;
