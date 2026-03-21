[out:json][timeout:30];
area["name:en"="Pristina"]->.outer;
(
  nwr["building"~"church"](area.outer);
  nwr["amenity"="place_of_worship"]["religion"="christian"](area.outer);
);
out geom;
