[out:json][timeout:30];
area["name:en"="Lima"]->.searchArea;
(
  nwr["amenity"="restaurant"](area.searchArea);
);
out geom;