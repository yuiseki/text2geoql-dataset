[out:json][timeout:30];
area["name:en"="Fuchu"]->.outer;
(
  nwr["amenity"="university"](area.outer);
);
out geom;
