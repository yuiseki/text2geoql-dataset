[out:json][timeout:30];
area["name:en"="Yau Tsim Mong District"]->.outer;
(
  nwr["amenity"~"hospital|clinic"](area.outer);
);
out geom;
