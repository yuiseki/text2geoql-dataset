[out:json][timeout:30];
area["name:en"="Wan Chai District"]->.outer;
(
  nwr["amenity"="university"](area.outer);
);
out geom;
