[out:json][timeout:30];
area["name:en"="Yau Tsim Mong District"]->.outer;
(
  nwr["amenity"~"pharmacy"](area.outer);
);
out geom;
