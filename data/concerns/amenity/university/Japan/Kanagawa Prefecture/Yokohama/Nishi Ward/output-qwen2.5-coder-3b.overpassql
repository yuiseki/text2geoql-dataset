[out:json][timeout:30];
area["name:en"="Yokohama"]->.outer;
(
  nwr["amenity"="university"](area.outer);
);
out geom;
