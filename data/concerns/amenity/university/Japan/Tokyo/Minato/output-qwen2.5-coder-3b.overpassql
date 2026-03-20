[out:json][timeout:30];
area["name:en"="Minato"]->.outer;
(
  nwr["amenity"="university"](area.outer);
);
out geom;
