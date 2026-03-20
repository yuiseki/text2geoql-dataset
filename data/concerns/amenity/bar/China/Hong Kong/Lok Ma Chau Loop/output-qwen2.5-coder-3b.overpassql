[out:json][timeout:30];
area["name:en"="Hong Kong"]->.outer;
(
  nwr["amenity"~"bar"](area.outer);
);
out geom;
