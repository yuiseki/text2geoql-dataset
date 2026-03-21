[out:json][timeout:30];
area["name:en"="Kowloon City District"]->.outer;
(
  nwr["building"~"church"](area.outer);
  nwr["amenity"="place_of_worship"]["religion"="christian"](area.outer);
);
out geom;
