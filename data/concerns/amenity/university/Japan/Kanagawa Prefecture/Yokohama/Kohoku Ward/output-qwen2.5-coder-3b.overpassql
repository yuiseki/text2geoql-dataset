[out:json][timeout:30];
area["name:en"="Kohoku Ward"]->.outer;
(
  nwr["amenity"="university"](area.outer);
);
out geom;
