[out:json][timeout:30];
area["name:en"="Tsuen Wan District"]->.outer;
(
  nwr["amenity"~"police"](area.outer);
);
out geom;
