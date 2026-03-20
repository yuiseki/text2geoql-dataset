[out:json][timeout:30];
area["name:en"="Tsuen Wan District"]->.outer;
(
  nwr["amenity"~"hospital"](area.outer);
);
out geom;
