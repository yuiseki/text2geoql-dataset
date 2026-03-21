[out:json][timeout:30];
area["name:en"="Hong Kong"]->.outer;
(
  nwr["amenity"~"clinic|doctor"](area.outer);
);
out geom;
