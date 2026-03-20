[out:json][timeout:30];
area["name:en"="Chiyoda"]->.outer;
(
  nwr["amenity"="university"](area.outer);
);
out geom;
