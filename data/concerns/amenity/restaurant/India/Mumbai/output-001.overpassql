[out:json][timeout:30];
area["name:en"="Mumbai"]->.searchArea;
(
  nwr["amenity"="restaurant"](area.searchArea);
);
out geom;