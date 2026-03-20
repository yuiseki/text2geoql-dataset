[out:json][timeout:30];
area["name:en"="Pristina"]->.outer;
(
  nwr["amenity"="university"](area.outer);
);
out geom;
