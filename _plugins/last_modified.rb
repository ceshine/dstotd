require 'date'

# Credit to https://github.com/mkiser/WTFJHT/blob/master/_plugins/last_modified.rb

module LastModified
  class Generator < Jekyll::Generator
    priority :highest
    def generate(site)
		@site = site
		@site.pages.each do |page|
			set_last_modified_date(page)
			# puts page.relative_path
		end

		@site.posts.docs.each do |post|
			set_last_modified_date(post)
			set_contribs(post)
			# puts post.relative_path
		end
    end

	def source(post_or_page)
		@site.source + "/" + post_or_page.relative_path
	end

	def contrib_source(contributors)
		@site.source + "/" + contributors.relative_path
	end

	def set_last_modified_date(post_or_page)
		entity_source = source(post_or_page)
		last_modified = `git log -1 --format="%at" -- "#{entity_source}"`
		last_modified.strip!
		post_or_page.data["last_modified"] = last_modified
	end

	def set_contribs(post)
		entity_source = contrib_source(post)

		contribs = `git log -- "#{entity_source}" | grep \^Author | sort | uniq | wc -l`
		contribs.strip!
		post.data["contributors"] = contribs
	end
  end
end
