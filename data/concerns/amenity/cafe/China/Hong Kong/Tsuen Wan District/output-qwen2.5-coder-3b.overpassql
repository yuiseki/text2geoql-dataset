[out:json][timeout:30];
area["name:en"="Tsuen Wan District"]->.outer;
(
  nwr["amenity"~"cafe"](area.outer);
);
out geom;
