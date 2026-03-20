[out:json][timeout:30];
area["name"="City of New York"]->.searchArea;
(
  nwr["amenity"="restaurant"]["cuisine"="ramen"](area.searchArea);
);
out geom;
