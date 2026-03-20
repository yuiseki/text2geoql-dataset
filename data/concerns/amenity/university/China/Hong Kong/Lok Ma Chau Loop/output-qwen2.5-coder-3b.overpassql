[out:json][timeout:30];
area["name:en"="Hong Kong"]->.outer;
(
  nwr["amenity"="university"](area.outer);
);
out geom;
