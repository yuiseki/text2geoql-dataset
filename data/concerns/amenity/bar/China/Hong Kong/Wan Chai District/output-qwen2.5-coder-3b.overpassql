[out:json][timeout:30];
area["name:en"="Wan Chai District"]->.outer;
(
  nwr["amenity"~"bar"](area.outer);
);
out geom;
