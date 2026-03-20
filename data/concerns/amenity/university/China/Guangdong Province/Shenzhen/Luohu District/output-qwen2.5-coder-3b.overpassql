[out:json][timeout:30];
area["name:en"="Shenzhen"]->.outer;
(
  nwr["amenity"="university"](area.outer);
);
out geom;
