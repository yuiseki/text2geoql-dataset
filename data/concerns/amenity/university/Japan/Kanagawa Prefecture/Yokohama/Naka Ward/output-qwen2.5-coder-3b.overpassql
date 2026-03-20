[out:json][timeout:30];
area["name:en"="Naka Ward"]->.outer;
(
  nwr["amenity"="university"](area.outer);
);
out geom;
