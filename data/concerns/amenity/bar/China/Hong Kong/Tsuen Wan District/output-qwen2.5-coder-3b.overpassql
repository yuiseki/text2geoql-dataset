[out:json][timeout:30];
area["name:en"="Tsuen Wan District"]->.outer;
(
  nwr["amenity"~"bar"](area.outer);
);
out geom;
