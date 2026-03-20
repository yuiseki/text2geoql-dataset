[out:json][timeout:30];
area["name:en"="Mitaka"]->.outer;
(
  nwr["amenity"="university"](area.outer);
);
out geom;
