[out:json][timeout:30];
area["name:en"="Hong Kong"]->.outer;
(
  nwr["amenity"~"dentist"](area.outer);
);
out geom;
