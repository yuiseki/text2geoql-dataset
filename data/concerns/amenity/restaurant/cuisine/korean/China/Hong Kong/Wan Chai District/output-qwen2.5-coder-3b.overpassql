[out:json][timeout:30];
area["name:en"="Wan Chai District"]->.outer;
(
  nwr["amenity"~"restaurant"]["cuisine"~"korean"](area.outer);
);
out geom;
