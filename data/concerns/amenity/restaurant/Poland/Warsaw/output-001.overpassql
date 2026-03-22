[out:json][timeout:30];
area["name:en"="Warsaw"]->.searchArea;
(
  nwr["amenity"="restaurant"](area.searchArea);
);
out geom;